import { Camera } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface NodeImageProps {
  imageUrl: string | null;
  name: string;
}

export function NodeImage({ imageUrl, name }: NodeImageProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Фото узла</CardTitle>
      </CardHeader>
      <CardContent>
        {imageUrl ? (
          <div className="overflow-hidden rounded-lg border border-border">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt={name}
              className="w-full object-cover max-h-64"
            />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border bg-muted/30 py-12">
            <Camera className="h-10 w-10 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Фото не загружено</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
